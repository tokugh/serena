using System;
using System.Collections.Generic;

namespace TestRepo
{
    public class ConcreteProcessor : BaseClass, IProcessable
    {
        private List<string> data;

        public ConcreteProcessor(string name) : base(name)
        {
            data = new List<string>();
        }

        public override void Execute()
        {
            Console.WriteLine($"Executing processor {name}");
            Process();
        }

        public void Process()
        {
            Console.WriteLine($"Processing data: {string.Join(", ", data)}");
        }

        public string GetType()
        {
            return "ConcreteProcessor";
        }

        public void AddData(string item)
        {
            data.Add(item);
        }
    }
}